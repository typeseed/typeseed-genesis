import uuid
from src.models import ColumnDefinition, ColumnProfileDefinition, TableDefinition
from src.producers.base_producer import BaseProducer
from transformers import AutoModelForCausalLM, AutoTokenizer

checkpoint = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
device = "cpu"  # for GPU usage or "cpu" for CPU usage


class SMOLLMProducer(BaseProducer):
    """Identifier producer class."""

    def generate(
        self,
        table_definition: TableDefinition,
        column_definition: ColumnDefinition,
        column_profile_definition: ColumnProfileDefinition,
        context: dict,
    ) -> str:
        
        model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)
        tokenizer = AutoTokenizer.from_pretrained(checkpoint)

        prompt = self.replace_placeholders(column_profile_definition.config.prompt, context)

        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=100)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)