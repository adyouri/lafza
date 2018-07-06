# Refactor jwt_header to accept username and password
# Test `test` cannot delete any term
# Test `author` can delete `author_term` but not `term`
# Test `admin` can delete both terms


# Test non-admin and non-author cannot delete term or translations
# Test author can delete term
# Test admin can delete term
# Test delete terms
# Delete translations
# Test delete translations

# Limit access to /register using flask-limiter
# Get register rate limit from REGISTER_LIMIT
# .flaskenv does not work with pytest for some reason
# Test Flask-Limiter (Global and /register)
# Use Redis as storage for Flask-Limiter
# Comment and DRY tests
