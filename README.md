# Job Hunt Agent

Automated job search and application pipeline tracker running on GitHub Actions.

## What's Included

1. **Daily Job Search** - Runs at 8 AM IST every weekday, searches 8 platforms
2. **Pipeline Tracker** - Full CRM for tracking applications from Applied to Offer

## Setup

1. Create a new private repository on GitHub
2. Upload all files to the repo root
3. Go to Actions tab - both workflows should appear automatically
4. Click "Daily Job Search" > Run workflow to test
5. Click "Pipeline Tracker" > Run workflow > select action to test

## Optional: Add OpenAI API Key

Settings > Secrets and variables > Actions > New repository secret
- Name: OPENAI_API_KEY
- Value: your API key (sk-...)

This enables AI-powered CV tailoring. Without it, basic keyword mode works fine.

## Cost

- Free on GitHub Free plan (uses ~70 minutes/month out of 2,000)
- Optional OpenAI API: Rs 90-150/month
