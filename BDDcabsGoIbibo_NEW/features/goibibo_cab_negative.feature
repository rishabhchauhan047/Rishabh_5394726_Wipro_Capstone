Feature: Goibibo cab negative validation coverage
  Negative tests are expected to pass when the invalid search is blocked.
  Each negative scenario records what was attempted and what happened.

  @negative @validation
  Scenario: Search is blocked when drop city is missing
    Given the user opens the Goibibo cab booking page
    When the user attempts a cab search without a drop city
      | pickup_query | pickup_suggestion      | pickup_date | pickup_time |
      | Delhi        | New Delhi, Delhi, India | tomorrow    | 10:00 AM    |
    Then the negative outcome "missing drop city" should be recorded
    And cab listing should not open

  @negative @validation
  Scenario: Search is blocked when drop city is typed but not selected
    Given the user opens the Goibibo cab booking page
    When the user attempts a cab search with an unselected drop city
      | pickup_query | pickup_suggestion      | invalid_drop_text | pickup_date    | pickup_time |
      | Delhi        | New Delhi, Delhi, India | Atlantis Nowhere  | today + 2 days | 11:00 AM    |
    Then the negative outcome "unselected invalid drop city" should be recorded
    And cab listing should not open
