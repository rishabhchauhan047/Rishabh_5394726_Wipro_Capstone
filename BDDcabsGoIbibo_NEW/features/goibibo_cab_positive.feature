Feature: Goibibo cab positive search and filter coverage
  Positive tests verify that searches, filters, and cab result cards work for
  different car preferences and journeys.

  @positive @filter @sedan @diesel
  Scenario: Search sedan diesel cabs from Delhi to Agra
    Given the user opens the Goibibo cab booking page
    When the user searches one-way cabs
      | pickup_query | pickup_suggestion      | drop_query | drop_suggestion           | pickup_date    | pickup_time |
      | Delhi        | New Delhi, Delhi, India | Agra       | Agra, Uttar Pradesh, India | today + 2 days | 11:00 AM    |
    And the user applies listing filters
      | filter | expected_result_text |
      | Sedan  | SEDAN                |
      | Diesel | Diesel               |
    Then available cab results should be displayed
    And the listing should reflect the applied filters
    When the user selects a cab matching "Dzire, Etios, Sedan"
    Then the cab review page should be displayed

  @positive @filter @suv @diesel
  Scenario: Search SUV diesel cabs from Mumbai to Pune
    Given the user opens the Goibibo cab booking page
    When the user searches one-way cabs
      | pickup_query | pickup_suggestion          | drop_query | drop_suggestion          | pickup_date    | pickup_time |
      | Mumbai       | Mumbai, Maharashtra, India | Pune       | Pune, Maharashtra, India | today + 3 days | 12:00 PM    |
    And the user applies listing filters
      | filter | expected_result_text |
      | SUV    | SUV                  |
      | Diesel | Diesel               |
    Then available cab results should be displayed
    And the listing should reflect the applied filters
    When the user selects a cab matching "Ertiga, Innova, SUV"
    Then the cab review page should be displayed

  @positive @filter @electric
  Scenario: Search electric cabs from Bangalore to Mysuru
    Given the user opens the Goibibo cab booking page
    When the user searches one-way cabs
      | pickup_query | pickup_suggestion           | drop_query | drop_suggestion          | pickup_date    | pickup_time |
      | Bangalore    | Bangalore, Karnataka, India | Mysuru     | Mysuru, Karnataka, India | today + 4 days | 01:00 PM    |
    And the user applies listing filters
      | filter   | expected_result_text |
      | Electric | Electric             |
    Then available cab results should be displayed
    And the listing should reflect the applied filters
    When the user selects a cab matching "BYD E6, Electric, EV"
    Then the cab review page should be displayed

  @positive @filter @petrol
  Scenario: Search petrol Innova Crysta cabs from Jaipur to Ajmer
    Given the user opens the Goibibo cab booking page
    When the user searches one-way cabs
      | pickup_query | pickup_suggestion         | drop_query | drop_suggestion        | pickup_date    | pickup_time |
      | Jaipur       | Jaipur, Rajasthan, India | Ajmer      | Ajmer, Rajasthan, India | today + 5 days | 02:00 PM    |
    And the user applies listing filters
      | filter         | expected_result_text |
      | Petrol         | Petrol               |
      | Innova Crysta  | Innova Crysta        |
    Then available cab results should be displayed
    And the listing should reflect the applied filters
    When the user selects a cab matching "Innova Crysta, Innova"
    Then the cab review page should be displayed

  @positive @different-city @ac
  Scenario: Search AC cabs from Delhi to Chandigarh
    Given the user opens the Goibibo cab booking page
    When the user searches one-way cabs
      | pickup_query | pickup_suggestion      | drop_query | drop_suggestion              | pickup_date    | pickup_time |
      | Delhi        | New Delhi, Delhi, India | Chandigarh | Chandigarh, Chandigarh, India | today + 6 days | 09:00 AM    |
    And the user applies listing filters
      | filter | expected_result_text |
      | Sedan  | SEDAN                |
    Then available cab results should be displayed
    And the listing should reflect the applied filters
    And the cab listing should mention "AC"
    When the user selects a cab matching "Dzire, Sedan"
    Then the cab review page should be displayed
