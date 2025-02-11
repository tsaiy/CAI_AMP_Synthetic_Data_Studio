class DummyBedrockClient:
    def converse(self, **kwargs):
        # Return a dummy response for the converse API.
        return {
            "score": 1.0,
            "justification": "Dummy converse response"
        }
    def invoke_model(self, modelId, body):
        # Return a dummy response for invoke_model.
        return [{
            "score": 1.0,
            "justification": "Dummy response from invoke_model"
        }]
    @property
    def meta(self):
        class Meta:
            region_name = "us-west-2"
        return Meta()
