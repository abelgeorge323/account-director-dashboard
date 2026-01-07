# Quick Deployment Guide to Heroku

## Prerequisites
- Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Have a Heroku account

## Step-by-Step Deployment

### 1. Login to Heroku
```bash
heroku login
```

### 2. Create a New Heroku App
```bash
heroku create account-director-dashboard
```
*Note: Replace `account-director-dashboard` with your preferred app name*

### 3. Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - Account Director Dashboard"
```

### 4. Add Heroku Remote (if created app separately)
```bash
heroku git:remote -a your-app-name
```

### 5. Deploy to Heroku
```bash
git push heroku main
```
*If your branch is named `master`, use:*
```bash
git push heroku master
```

### 6. Open Your App
```bash
heroku open
```

## Verify Deployment

Your app should open in your browser at `https://your-app-name.herokuapp.com`

## Updating the App

After making changes:
```bash
git add .
git commit -m "Description of changes"
git push heroku main
```

## View Logs

To troubleshoot issues:
```bash
heroku logs --tail
```

## Common Issues

### CSV File Not Found
Ensure `data/performance_reviews.csv` is committed to git and exists in the repository.

### Port Binding Error
The app automatically uses Heroku's `$PORT` environment variable. No configuration needed.

### Build Failed
Check that:
- `requirements.txt` is present and correct
- `runtime.txt` specifies Python 3.11.9
- `Procfile` is present with the correct command

## App Configuration

The following files configure Heroku deployment:
- **Procfile**: Defines the web process command
- **runtime.txt**: Specifies Python version (3.11.9)
- **requirements.txt**: Lists Python dependencies
- **.streamlit/config.toml**: Streamlit configuration

## Support

For Heroku-specific issues, see: https://devcenter.heroku.com/articles/getting-started-with-python

For Streamlit deployment, see: https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app

