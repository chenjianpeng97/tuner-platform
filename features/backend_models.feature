Feature: Backend models are reusable in BDD steps

  Scenario: Import Username value object from backend package
    Given backend model "Username" is imported
    When I create username with value "bdd_user"
    Then username value should be "bdd_user"
