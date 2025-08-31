# AI Parser service
# AI-powered transaction extraction from text

import os
import json
import logging
from typing import List, Dict, Any
from openai import AzureOpenAI
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_with_ai(text: str) -> List[Dict[str, Any]]:
    """
    Use Azure AI to extract transactions from text

    Args:
        text: Raw text content

    Returns:
        List of transaction dictionaries
    """
    logger.info("Starting AI transaction extraction")

    try:
        transactions = extract_transactions_with_ai(text)
        logger.info(f"Successfully extracted {len(transactions)} transactions")
        return transactions
    except Exception as e:
        logger.error(f"AI parsing failed: {e}")
        # Fallback to mock data if AI fails
        return [{
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": "AI Parsing Failed - Fallback Transaction",
            "amount": -123.45,
            "category": "Uncategorized"
        }]

def extract_transactions_with_ai(text: str) -> List[Dict[str, Any]]:
    """
    Use Azure AI to extract transactions from text

    Args:
        text: Raw text content

    Returns:
        List of transaction dictionaries
    """
    logger.info("Starting Azure AI transaction extraction")

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Create the prompt for transaction extraction
    prompt = create_transaction_extraction_prompt(text)

    # Make the API call
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    logger.info(f"Making Azure AI API call with deployment: {deployment_name}")

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": "Extract transactions from credit card statements. Return JSON array with date, description, amount, category."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_completion_tokens=10000
    )

    # Parse the response
    ai_response = response.choices[0].message.content.strip()
    logger.info(f"Received AI response of {len(ai_response)} characters")

    # Try to extract JSON from the response
    try:
        # Look for JSON array in the response
        json_start = ai_response.find('[')
        json_end = ai_response.rfind(']') + 1

        if json_start != -1 and json_end != -1:
            json_content = ai_response[json_start:json_end]
            transactions = json.loads(json_content)

            # Validate and clean the transactions
            cleaned_transactions = validate_and_clean_transactions(transactions)
            logger.info(f"Successfully processed {len(cleaned_transactions)} transactions")
            return cleaned_transactions
        else:
            logger.warning("No JSON array found in AI response")
            return []

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        logger.debug(f"AI Response length: {len(ai_response)} characters, first 100 chars: {ai_response[:100]}...")
        return []

def create_transaction_extraction_prompt(text: str) -> str:
    """
    Create a prompt for transaction extraction

    Args:
        text: Raw text content

    Returns:
        Formatted prompt for AI
    """
    return f"""Extract all transactions from this credit card statement.

Return as JSON array:
[
  {{
    "date": "YYYY-MM-DD",
    "description": "merchant name",
    "amount": -123.45,
    "category": "Groceries|Restaurants|Shopping|Transportation|Medical|Bills|Other"
  }}
]

Text:
{text[:4000]}
"""

def validate_and_clean_transactions(transactions: List[Dict]) -> List[Dict[str, Any]]:
    """
    Validate and clean extracted transactions

    Args:
        transactions: Raw transactions from AI

    Returns:
        Cleaned and validated transactions
    """
    logger.info(f"Validating and cleaning {len(transactions)} transactions")
    cleaned_transactions = []

    for tx in transactions:
        try:
            # Basic validation
            if not isinstance(tx, dict) or 'date' not in tx or 'description' not in tx or 'amount' not in tx:
                continue

            # Clean date
            date_str = str(tx['date']).strip()
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")

            # Clean description
            description = str(tx['description']).strip()
            if not description:
                description = "Transaction"

            # Clean amount
            try:
                amount = float(tx['amount'])
            except (ValueError, TypeError):
                amount = 0.0

            # Clean category
            category = str(tx.get('category', 'Other')).strip()
            if not category:
                category = 'Other'

            cleaned_tx = {
                "date": date_str,
                "description": description,
                "amount": amount,
                "category": category
            }

            cleaned_transactions.append(cleaned_tx)

        except Exception as e:
            logger.warning(f"Skipping invalid transaction: {e}")
            continue

    logger.info(f"Validation complete. Kept {len(cleaned_transactions)} of {len(transactions)} transactions")
    return cleaned_transactions
