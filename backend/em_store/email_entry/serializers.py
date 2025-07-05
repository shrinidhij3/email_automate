from rest_framework import serializers
from .models import EmailEntry
from campaigns.serializers import EmailCampaignSerializer

class EmailEntrySerializer(serializers.ModelSerializer):
    campaign = serializers.PrimaryKeyRelatedField(
        queryset=EmailEntry._meta.get_field('campaign').remote_field.model.objects.all(),
        required=False,
        allow_null=True,
        help_text="ID of the associated campaign"
    )
    
    class Meta:
        model = EmailEntry
        fields = [
            'id', 'name', 'email', 'client_email', 'date_of_signup',
            'day_one', 'day_two', 'day_four', 'day_five',
            'day_seven', 'day_nine', 'campaign', 'unsubscribe'
        ]
        read_only_fields = [
            'id', 'date_of_signup', 'day_one', 'day_two',
            'day_four', 'day_five', 'day_seven', 'day_nine'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'client_email': {'required': False, 'allow_blank': True, 'allow_null': True}
        }
