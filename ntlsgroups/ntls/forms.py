from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Consumer, Business, Feedback
import os
import phonenumbers
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'contact', 'services']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., John Doe'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., john@example.com'})
        self.fields['services'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Web Development, Consulting', 'rows': 3})

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, contact):
            raise ValidationError('Please enter a valid email address.')
        return contact

class BusinessForm(forms.ModelForm):
    country_code = forms.ChoiceField(
        choices=[(code, f"{code} ({country})") for code, country in [
            ("+93", "Afghanistan"), ("+355", "Albania"), ("+213", "Algeria"), ("+1-684", "American Samoa"),
            ("+376", "Andorra"), ("+244", "Angola"), ("+1-264", "Anguilla"), ("+1-268", "Antigua and Barbuda"),
            ("+54", "Argentina"), ("+374", "Armenia"), ("+297", "Aruba"), ("+61", "Australia"), ("+43", "Austria"),
            ("+994", "Azerbaijan"), ("+1-242", "Bahamas"), ("+973", "Bahrain"), ("+880", "Bangladesh"),
            ("+1-246", "Barbados"), ("+375", "Belarus"), ("+32", "Belgium"), ("+501", "Belize"), ("+229", "Benin"),
            ("+1-441", "Bermuda"), ("+975", "Bhutan"), ("+591", "Bolivia"), ("+387", "Bosnia and Herzegovina"),
            ("+267", "Botswana"), ("+55", "Brazil"), ("+246", "British Indian Ocean Territory"),
            ("+1-284", "British Virgin Islands"), ("+673", "Brunei"), ("+359", "Bulgaria"), ("+226", "Burkina Faso"),
            ("+257", "Burundi"), ("+855", "Cambodia"), ("+237", "Cameroon"), ("+1", "Canada"), ("+238", "Cape Verde"),
            ("+1-345", "Cayman Islands"), ("+236", "Central African Republic"), ("+235", "Chad"), ("+56", "Chile"),
            ("+86", "China"), ("+61", "Christmas Island"), ("+61", "Cocos Islands"), ("+57", "Colombia"),
            ("+269", "Comoros"), ("+242", "Congo"), ("+243", "Congo (DRC)"), ("+682", "Cook Islands"),
            ("+506", "Costa Rica"), ("+225", "Côte d'Ivoire"), ("+385", "Croatia"), ("+53", "Cuba"), ("+599", "Curaçao"),
            ("+357", "Cyprus"), ("+420", "Czech Republic"), ("+45", "Denmark"), ("+253", "Djibouti"),
            ("+1-767", "Dominica"), ("+1-809", "Dominican Republic"), ("+670", "East Timor"), ("+593", "Ecuador"),
            ("+20", "Egypt"), ("+503", "El Salvador"), ("+240", "Equatorial Guinea"), ("+291", "Eritrea"),
            ("+372", "Estonia"), ("+251", "Ethiopia"), ("+500", "Falkland Islands"), ("+298", "Faroe Islands"),
            ("+679", "Fiji"), ("+358", "Finland"), ("+33", "France"), ("+594", "French Guiana"),
            ("+689", "French Polynesia"), ("+241", "Gabon"), ("+220", "Gambia"), ("+995", "Georgia"), ("+49", "Germany"),
            ("+233", "Ghana"), ("+350", "Gibraltar"), ("+30", "Greece"), ("+299", "Greenland"), ("+1-473", "Grenada"),
            ("+590", "Guadeloupe"), ("+1-671", "Guam"), ("+502", "Guatemala"), ("+44-1481", "Guernsey"),
            ("+224", "Guinea"), ("+245", "Guinea-Bissau"), ("+592", "Guyana"), ("+509", "Haiti"), ("+504", "Honduras"),
            ("+852", "Hong Kong"), ("+36", "Hungary"), ("+354", "Iceland"), ("+91", "India"), ("+62", "Indonesia"),
            ("+98", "Iran"), ("+964", "Iraq"), ("+353", "Ireland"), ("+44-1624", "Isle of Man"), ("+972", "Israel"),
            ("+39", "Italy"), ("+1-876", "Jamaica"), ("+81", "Japan"), ("+44-1534", "Jersey"), ("+962", "Jordan"),
            ("+7", "Kazakhstan"), ("+254", "Kenya"), ("+686", "Kiribati"), ("+383", "Kosovo"), ("+965", "Kuwait"),
            ("+996", "Kyrgyzstan"), ("+856", "Laos"), ("+371", "Latvia"), ("+961", "Lebanon"), ("+266", "Lesotho"),
            ("+231", "Liberia"), ("+218", "Libya"), ("+423", "Liechtenstein"), ("+370", "Lithuania"),
            ("+352", "Luxembourg"), ("+853", "Macau"), ("+389", "Macedonia"), ("+261", "Madagascar"),
            ("+265", "Malawi"), ("+60", "Malaysia"), ("+960", "Maldives"), ("+223", "Mali"), ("+356", "Malta"),
            ("+692", "Marshall Islands"), ("+222", "Mauritania"), ("+230", "Mauritius"), ("+262", "Mayotte"),
            ("+52", "Mexico"), ("+691", "Micronesia"), ("+1-808", "Midway Island"), ("+373", "Moldova"),
            ("+377", "Monaco"), ("+976", "Mongolia"), ("+382", "Montenegro"), ("+1-664", "Montserrat"),
            ("+212", "Morocco"), ("+258", "Mozambique"), ("+95", "Myanmar"), ("+264", "Namibia"), ("+674", "Nauru"),
            ("+977", "Nepal"), ("+31", "Netherlands"), ("+599", "Netherlands Antilles"), ("+1-869", "Nevis"),
            ("+687", "New Caledonia"), ("+64", "New Zealand"), ("+505", "Nicaragua"), ("+227", "Niger"),
            ("+234", "Nigeria"), ("+683", "Niue"), ("+850", "North Korea"), ("+1-670", "Northern Mariana Islands"),
            ("+47", "Norway"), ("+968", "Oman"), ("+92", "Pakistan"), ("+680", "Palau"), ("+970", "Palestinian Territory"),
            ("+507", "Panama"), ("+675", "Papua New Guinea"), ("+595", "Paraguay"), ("+51", "Peru"), ("+63", "Philippines"),
            ("+48", "Poland"), ("+351", "Portugal"), ("+1-787", "Puerto Rico"), ("+974", "Qatar"), ("+242", "Réunion"),
            ("+40", "Romania"), ("+7", "Russia"), ("+250", "Rwanda"), ("+590", "Saint Barthélemy"),
            ("+290", "Saint Helena"), ("+1-869", "Saint Kitts and Nevis"), ("+1-758", "Saint Lucia"),
            ("+590", "Saint Martin"), ("+508", "Saint Pierre and Miquelon"), ("+1-784", "Saint Vincent and the Grenadines"),
            ("+685", "Samoa"), ("+378", "San Marino"), ("+239", "São Tomé and Príncipe"), ("+966", "Saudi Arabia"),
            ("+221", "Senegal"), ("+381", "Serbia"), ("+248", "Seychelles"), ("+232", "Sierra Leone"),
            ("+65", "Singapore"), ("+1-721", "Sint Maarten"), ("+421", "Slovakia"), ("+386", "Slovenia"),
            ("+677", "Solomon Islands"), ("+252", "Somalia"), ("+27", "South Africa"), ("+82", "South Korea"),
            ("+211", "South Sudan"), ("+34", "Spain"), ("+94", "Sri Lanka"), ("+249", "Sudan"), ("+597", "Suriname"),
            ("+47", "Svalbard and Jan Mayen"), ("+268", "Swaziland"), ("+46", "Sweden"), ("+41", "Switzerland"),
            ("+963", "Syria"), ("+886", "Taiwan"), ("+992", "Tajikistan"), ("+255", "Tanzania"), ("+66", "Thailand"),
            ("+670", "Timor-Leste"), ("+228", "Togo"), ("+690", "Tokelau"), ("+676", "Tonga"),
            ("+1-868", "Trinidad and Tobago"), ("+216", "Tunisia"), ("+90", "Turkey"), ("+993", "Turkmenistan"),
            ("+1-649", "Turks and Caicos Islands"), ("+688", "Tuvalu"), ("+1-340", "U.S. Virgin Islands"),
            ("+256", "Uganda"), ("+380", "Ukraine"), ("+971", "United Arab Emirates"), ("+44", "United Kingdom"),
            ("+1", "United States"), ("+598", "Uruguay"), ("+998", "Uzbekistan"), ("+678", "Vanuatu"), ("+58", "Venezuela"),
            ("+84", "Vietnam"), ("+1-808", "Wake Island"), ("+681", "Wallis and Futuna"), ("+967", "Yemen"),
            ("+260", "Zambia"), ("+263", "Zimbabwe")
        ]],
        initial="+91",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Business
        fields = ['name', 'contact', 'state', 'district', 'business_mode', 'category', 'contact_number', 'applier_designation', 'registration_proof', 'address_proof', 'logo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., NTLS Solutions'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., info@ntls.com'})
        self.fields['state'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Tamilnadu'})
        self.fields['district'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Namakkal'})
        self.fields['business_mode'].widget.attrs.update({'class': 'form-select'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['contact_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., 9629828969'})
        self.fields['applier_designation'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., CEO'})
        self.fields['registration_proof'].widget.attrs.update({'class': 'form-control'})
        self.fields['address_proof'].widget.attrs.update({'class': 'form-control'})
        self.fields['logo'].widget.attrs.update({'class': 'form-control'})

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, contact):
            raise ValidationError('Please enter a valid email address.')
        return contact

    def clean_contact_number(self):
        contact_number = self.cleaned_data['contact_number']
        if contact_number:
            normalized_value = contact_number.replace(' ', '').replace('-', '')
            if not normalized_value.isdigit() or len(normalized_value) < 6 or len(normalized_value) > 15:
                raise ValidationError('Contact number must contain only digits and be 6-15 digits long.')
        return contact_number

    def clean_registration_proof(self):
        registration_proof = self.cleaned_data['registration_proof']
        if registration_proof:
            ext = os.path.splitext(registration_proof.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError('Only PDF files are allowed for registration proof.')
        return registration_proof

    def clean_address_proof(self):
        address_proof = self.cleaned_data['address_proof']
        if address_proof:
            ext = os.path.splitext(address_proof.name)[1].lower()
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError('Only PDF, JPG, JPEG, or PNG files are allowed for address proof.')
        return address_proof

    def clean_logo(self):
        logo = self.cleaned_data['logo']
        if logo:
            ext = os.path.splitext(logo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError('Only JPG, JPEG, or PNG files are allowed for logo.')
            if logo.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('Logo file size must be under 5MB.')
        return logo

    def clean(self):
        cleaned_data = super().clean()
        country_code = cleaned_data.get("country_code")
        contact_number = cleaned_data.get("contact_number")
        if contact_number and country_code:
            full_contact = f"{country_code}{contact_number}"
            logger.debug(f"Validating full contact number: {full_contact}")
            try:
                # Extract the country code prefix (e.g., +91) to infer the region
                country_code_prefix = country_code.lstrip('+')
                region = phonenumbers.region_code_for_country_code(int(country_code_prefix)) if country_code_prefix.isdigit() else None
                parsed_number = phonenumbers.parse(full_contact, region) if region else phonenumbers.parse(full_contact, None)
                if not phonenumbers.is_valid_number(parsed_number):
                    logger.warning(f"Invalid phone number for region {region}: {full_contact}")
                    raise ValidationError('The full contact number is not a valid international phone number. Contact number must be in a valid international format (e.g., +911234567890, +1-123-456-7890, or +442071234567).')
                # Format the number for storage (e.g., E.164 format)
                cleaned_data['full_contact'] = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                logger.debug(f"Validated and formatted full contact: {cleaned_data['full_contact']}")
            except phonenumbers.phonenumberutil.NumberParseException as e:
                logger.error(f"Phone number parse error for {full_contact} with region {region}: {str(e)}")
                raise ValidationError('The full contact number could not be parsed. Please check the format and ensure it matches the selected country code.')
            except ValueError as e:
                logger.error(f"Value error during parsing {full_contact}: {str(e)}")
                raise ValidationError('Invalid country code or number format.')
        return cleaned_data

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Jane Smith'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., jane@example.com'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Your feedback here', 'rows': 4})

    def clean_email(self):
        email = self.cleaned_data['email']
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            raise ValidationError('Please enter a valid email address.')
        return email