# Test `test` cannot delete any translation
# Test `author` can delete `author_translation` but not `translation`
# Test `admin` can delete both translations

# Use Redis as storage for Flask-Limiter
# Comment and DRY tests

# Limit access to /register using flask-limiter
# Get register rate limit from REGISTER_LIMIT
# .flaskenv does not work with pytest for some reason
# Test Flask-Limiter (Global and /register)
