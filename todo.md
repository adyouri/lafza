# Test Unupvoting resets the score to 1


# Add /translations/<id>/downvote
# Test /translations/<id>/downvote

# If already upvoted, unupvote
# If already downvoted, undownvote

# Move upvote()/downvote() to `models.Translation`
# Update score when upvoted/downvoted

# Delete translations
# Delete terms (only admins and authors can delete terms)
# Test non-admin and non-author cannot delete term or translations
# Test delete terms
# Test delete translations

# Limit access to /register using flask-limiter
# Get register rate limit from REGISTER_LIMIT
# .flaskenv does not work with pytest for some reason
# Test Flask-Limiter (Global and /register)
# Use Redis as storage for Flask-Limiter
# Comment and DRY tests
