# Tempus Vestis - An AI powered wardrobe planner

Tempus Vestis is an AI powered application to help determine what to pack. The application will provide
a user with a recommended packing list for a destination and timeframe.

When given a prompt, the application will use tools to determine a date range and appropriate parameters
for a weather API to get the forecast for the dates. With the dates and forecast, the LLM will provide
reasonable suggestions for the weather conditions.

## External API

National Weather Service API - This is a free API for US based locations only. The LLM should validate
the user input to ensure that the destination is within the US.
