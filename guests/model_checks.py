from guests import *


@validation.GuestMerch
def is_merch_checklist_complete(guest_merch):
    if not guest_merch.selling_merch:
        return 'You need to tell us whether and how you want to sell merchandise'

    elif guest_merch.selling_merch == c.ROCK_ISLAND:
        if not guest_merch.inventory:
            return 'You must add some merch to your inventory!'

        elif not guest_merch.poc_is_group_leader and not (
                guest_merch.poc_first_name and
                guest_merch.poc_last_name and
                guest_merch.poc_phone and
                guest_merch.poc_email):
            return 'You must tell us about your merch point of contact'

        elif not (
                guest_merch.poc_zip_code and
                guest_merch.poc_address1 and
                guest_merch.poc_city and
                guest_merch.poc_region and
                guest_merch.poc_country):
            return 'You must tell us your complete mailing address'
