# HKPUG-Meetup82-StructuredOutputWithLLM

## Introduction
This is the repository for the talk "Structured Output with LLM" in HKPUG Meetup 82. The talk is about how to use language model to generate structured output with latest frameworks.

The frameworks covered in the talk are:
- [Instructor](https://github.com/instructor-ai/instructor)
- [BoundaryML (BAML)](https://github.com/BoundaryML/baml)

## Slides
You can find the slides in [here](https://1drv.ms/p/c/40f756128322ebe1/EZt6Z1aMFF1DkSFLkkVBeFsBduE-D5dRcPyDVmKUE-ETHw).

## Examples
This repository contains 5 examples to demonstrate how to use LLM to generate structured output with Instructor and BAML.
- [Instructor Basic](src/example-1-instructor-basics/main.py): Basic example to generate structured output with Instructor.
- [Instructor Streaming](src/example-2-instructor-streaming/backend/main.py): Example to generate structured output with Instructor in streaming mode.
- [Instructor With Enum](src/example-3-instructor-enum/main.py): Example to generate structured output with Instructor with enum.
- [Instructor With Completions](src/example-4-instructor-completions/main.py): Example to generate structured output with Instructor token usages statistics.
- [BAML](src/example-5-baml/main.py): Example to generate structured output with BAML.

All the examples can be run via the Makefile. You can run the examples by running the following command:
```bash
make run_example_<X>
```
where `<X>` is the example number.

## Requirements
- Fireworks API Key: You need to have a Fireworks API key to run the examples.
