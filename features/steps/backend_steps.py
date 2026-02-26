from behave import given, then, when

from app.domain.value_objects.username import Username


@given('backend model "Username" is imported')
def step_import_username(context) -> None:
    context.username_class = Username


@when('I create username with value "{value}"')
def step_create_username(context, value: str) -> None:
    context.username = context.username_class(value=value)


@then('username value should be "{value}"')
def step_assert_username_value(context, value: str) -> None:
    assert context.username.value == value
