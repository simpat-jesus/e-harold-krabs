# Categorizer service
# AI-powered transaction categorization

import os
import logging
from typing import Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

def categorize_transaction(description: str, amount: float) -> str:
    """Use Azure AI to categorize a transaction based on description and amount."""
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        # Determine if it's income or expense for better categorization
        transaction_type = "income" if amount > 0 else "expense"

        prompt = f"""
        Categorize this financial transaction:
        Description: {description}
        Amount: ${amount:.2f}
        Type: {transaction_type}

        Categories: Food, Transportation, Entertainment, Utilities, Rent, Salary, Shopping, Healthcare, Education, Travel, Insurance, Subscriptions, Other

        Return only the category name that best fits this transaction.
        """

        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.1
        )

        category = response.choices[0].message.content.strip()

        # Validate the category
        valid_categories = ["Food", "Transportation", "Entertainment", "Utilities", "Rent", "Salary", "Shopping", "Healthcare", "Education", "Travel", "Insurance", "Subscriptions", "Other"]

        if category in valid_categories:
            logger.info(f"Transaction successfully categorized as '{category}'")
            return category
        else:
            logger.warning(f"AI returned invalid category '{category}', using 'Other'")
            return "Other"

    except Exception as e:
        logger.error(f"AI categorization failed: {e}")
        return "Uncategorized"

def batch_categorize_transactions(transactions: list) -> list:
    """Categorize multiple transactions efficiently."""
    categorized = []
    for tx in transactions:
        category = categorize_transaction(tx["description"], tx["amount"])
        tx_copy = tx.copy()
        tx_copy["category"] = category
        categorized.append(tx_copy)
    return categorized
