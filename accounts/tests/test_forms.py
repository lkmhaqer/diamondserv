"""
file: accounts/tests/test_forms.py
author: lkmhaqer

We want to test the invite system for the most part
in this module. Most of the complexity is in how the
InviteUserRegistrationForm() extends a normal
UserRegistrationForm() with a field for a uuid invite_token.
This field must be validated in clean(), as an existing
InviteCode(). Once validated, we must update the InviteCode()
with used=True during InviteUserRegistrationForm.save().
"""
