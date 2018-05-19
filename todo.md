# Use Redis for blacklisting
# Use __in__ magic method to make the redis server behave like a python list
# Test that black listed token expire in redis after 3 seconds (refresh lifespan)
# Follow https://www.python.org/dev/peps/pep-0257/
# Comment and DRY tests
# Update to Flask 1.0
# Limit access to /register using flask-limiter
