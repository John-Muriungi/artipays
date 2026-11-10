from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "name",
            "description",
            "venue",
            "location",
            "event_date",
            "start_time",
            "end_time",
            "song_request_price",
            "minimum_tip",
            "status",
        )
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        data = super().clean()
        if data.get("song_request_price", 0) < 1:
            self.add_error("song_request_price", "Request price must be at least KES 1.")
        if data.get("minimum_tip", 0) < 0:
            self.add_error("minimum_tip", "Minimum tip cannot be negative.")
        return data
