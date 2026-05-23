from behave import given, then, when


def _single_row(table):
    assert table is not None and len(table.rows) == 1, "Step requires exactly one data row."
    return table.rows[0].as_dict()


@given("the user opens the Goibibo cab booking page")
def step_open_cab_page(context):
    context.cabs.open_home_page()


@when('the user selects "{trip_type}" cab trip')
def step_select_trip_type(context, trip_type):
    context.cabs.select_trip_type(trip_type)


@when("the user searches one-way cabs")
def step_search_one_way_cabs(context):
    row = _single_row(context.table)
    context.cabs.search_one_way_route(
        pickup_query=row["pickup_query"],
        pickup_suggestion=row["pickup_suggestion"],
        drop_query=row["drop_query"],
        drop_suggestion=row["drop_suggestion"],
        pickup_date=row["pickup_date"],
        pickup_time=row["pickup_time"],
    )


@when("the user applies listing filters")
def step_apply_listing_filters(context):
    context.applied_filters = []
    context.unavailable_filters = []
    for row in context.table:
        outcome = context.cabs.apply_listing_filter(
            option=row["filter"],
            expected_result_text=row["expected_result_text"],
        )
        if outcome["applied"]:
            context.applied_filters.append(outcome)
        else:
            context.unavailable_filters.append(outcome)


@when('the user selects a cab matching "{cab_preference}"')
def step_select_matching_cab(context, cab_preference):
    context.cabs.select_cab(cab_preference)


@when("the user fills anonymous traveller details")
def step_fill_anonymous_traveller_details(context):
    row = _single_row(context.table)
    context.traveller_details = row
    context.cabs.fill_anonymous_traveller_details(
        pickup_location=row["pickup_location"],
        full_name=row["full_name"],
        mobile=row["mobile"],
        email=row["email"],
    )


@when("the user continues to payment")
def step_continue_to_payment(context):
    context.cabs.continue_to_payment()


@when("the user selects UPI payment option")
def step_select_upi_payment(context):
    context.cabs.select_upi_payment_option()


@when("the user clicks Generate QR")
def step_click_generate_qr(context):
    context.cabs.click_generate_qr()


@when("the user attempts a cab search without a drop city")
def step_attempt_missing_drop_search(context):
    row = _single_row(context.table)
    context.negative_outcome = context.cabs.attempt_search_without_drop_city(
        pickup_query=row["pickup_query"],
        pickup_suggestion=row["pickup_suggestion"],
        pickup_date=row["pickup_date"],
        pickup_time=row["pickup_time"],
    )


@when("the user attempts a cab search with an unselected drop city")
def step_attempt_unselected_drop_search(context):
    row = _single_row(context.table)
    context.negative_outcome = context.cabs.attempt_search_with_unselected_drop_city(
        pickup_query=row["pickup_query"],
        pickup_suggestion=row["pickup_suggestion"],
        invalid_drop_text=row["invalid_drop_text"],
        pickup_date=row["pickup_date"],
        pickup_time=row["pickup_time"],
    )


@then("available cab results should be displayed")
def step_verify_results(context):
    context.cabs.verify_cab_results_displayed()


@then("the listing should reflect the applied filters")
def step_verify_applied_filters(context):
    context.cabs.verify_listing_reflects_filters(getattr(context, "applied_filters", []))


@then('the cab listing should mention "{expected_text}"')
def step_verify_listing_mentions(context, expected_text):
    context.cabs.verify_listing_mentions(expected_text)


@then('the results should be for pickup "{pickup}" and drop "{drop}"')
def step_verify_route(context, pickup, drop):
    context.cabs.verify_route_details(pickup, drop)


@then("the cab review page should be displayed")
def step_verify_review_page(context):
    context.cabs.verify_review_page_displayed()


@then("the anonymous traveller details should remain filled")
def step_verify_anonymous_details(context):
    details = context.traveller_details
    context.cabs.verify_anonymous_traveller_details(
        pickup_location=details["pickup_location"],
        full_name=details["full_name"],
        mobile=details["mobile"],
        email=details["email"],
    )


@then("the UPI QR payment request should be displayed")
def step_verify_upi_qr(context):
    context.cabs.verify_upi_qr_displayed()


@then("no actual payment should be completed")
def step_verify_no_actual_payment(context):
    context.cabs.verify_no_actual_payment_completed()


@then('the negative outcome "{case_name}" should be recorded')
def step_record_negative_outcome(context, case_name):
    context.cabs.record_negative_outcome(context, case_name)


@then("cab listing should not open")
def step_verify_listing_not_opened(context):
    context.cabs.verify_listing_not_opened()
