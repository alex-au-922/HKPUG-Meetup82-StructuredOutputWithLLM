include .env
run_example_1:
	docker build -t hkpug-example-1-instructor-basics \
		src/example-1-instructor-basics
	docker run --env-file .env \
		hkpug-example-1-instructor-basics
run_example_2:
	cd src/example-2-instructor-streaming && \
	docker compose up --build
run_example_3:
	docker build -t hkpug-example-3-instructor-enum \
		src/example-3-instructor-enum
	docker run --env-file .env \
		hkpug-example-3-instructor-enum
run_example_4:
	docker build -t hkpug-example-4-instructor-with-completions \
		src/example-4-instructor-with-completions
	docker run --env-file .env \
		hkpug-example-4-instructor-with-completions
run_example_5:
	docker build -t hkpug-example-5-baml \
		src/example-5-baml
	docker run --env-file .env \
		hkpug-example-5-baml