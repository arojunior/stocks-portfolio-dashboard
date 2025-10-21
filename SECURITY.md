# Security Guidelines

## ⚠️ CRITICAL: No Personal Data in Code

**NEVER commit personal data to the repository!**

### What NOT to commit:
- API tokens/keys
- Personal usernames
- Phone numbers
- Bot tokens
- Any sensitive credentials

### What TO do:
- Use environment variables only
- Store sensitive data in `.env` file (gitignored)
- Use generic placeholders in documentation
- Use `env.template` as a guide

## Environment Variables

Copy `env.template` to `.env` and fill in your actual values:

```bash
cp env.template .env
```

## Telegram Bot Setup

1. Create a bot with @BotFather
2. Get your bot token
3. Add token to `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_token_here
   TELEGRAM_BOT_USERNAME=your_actual_username_here
   ```

## If You Accidentally Commit Sensitive Data

1. **Immediately** remove the data from code
2. **Regenerate** any exposed tokens/keys
3. **Force push** to remove from git history
4. **Check** if data was already pulled by others

## Security Checklist

- [ ] No hardcoded tokens in code
- [ ] All sensitive data in `.env` only
- [ ] `.env` file is gitignored
- [ ] Documentation uses placeholders
- [ ] No personal data in commit history
