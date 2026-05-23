Feature: Goibibo cab end to end UPI QR flow
  The end to end test reaches the review page, fills anonymous traveller details,
  opens payment, selects UPI, and stops after the QR request is displayed.

  @e2e @positive @review
  Scenario: End to end one-way cab UPI QR flow for Delhi to Agra
    Given the user opens the Goibibo cab booking page
    When the user searches one-way cabs
      | pickup_query | pickup_suggestion        | drop_query | drop_suggestion           | pickup_date | pickup_time |
      | Delhi        | New Delhi, Delhi, India   | Agra       | Agra, Uttar Pradesh, India | tomorrow    | 10:00 AM    |
    And the user applies listing filters
      | filter    | expected_result_text |
      | Hatchback | HATCHBACK             |
      | Cng       | CNG                   |
    Then available cab results should be displayed
    And the listing should reflect the applied filters
    When the user selects a cab matching "WagonR, Swift"
    Then the cab review page should be displayed
    When the user fills anonymous traveller details
      | pickup_location                    | full_name           | mobile     | email                         |
      | India Gate, New Delhi, Delhi, India | Anonymous Traveller | 9876543210 | anonymous.traveller@test.com  |
    Then the anonymous traveller details should remain filled
    When the user continues to payment
    And the user selects UPI payment option
    And the user clicks Generate QR
    Then the UPI QR payment request should be displayed
    And no actual payment should be completed
