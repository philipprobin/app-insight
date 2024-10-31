class CostCalculator:
    INPUT_COST = 0.150 / 1_000_000  # $0.15 per million input tokens
    OUTPUT_COST = 0.6 / 1_000_000  # $0.60 per million output tokens
    CACHED_INPUT_COST = 0.075 / 1_000_000  # $0.075 per million cached input tokens

    @staticmethod
    def calculate_api_cost(input_tokens: int, output_tokens: int, cached: bool = False) -> float:
        """
        Calculate the cost based on the number of input and output tokens.
        If `cached` is True, a lower cost is applied for cached input tokens.
        """
        input_cost = (CostCalculator.CACHED_INPUT_COST if cached else CostCalculator.INPUT_COST) * input_tokens
        output_cost = CostCalculator.OUTPUT_COST * output_tokens
        return input_cost + output_cost
