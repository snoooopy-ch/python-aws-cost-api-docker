# python-aws-cost-api-docker

steps to run the sample rest service on docker -

1. Move to the directory - cd python-aws-cost-api-docker

2. Build the docker image - docker build -t aws-cost-rest .

3. Create and run a container - docker run -d -p 5000:5000 aws-cost-rest

4. Navigate to http://0.0.0.0:5000/ to get hello world'd

A Sample Client --

curl --location --request POST 'http://localhost:5000/api/v1/cost' 
--header 'Content-Type: application/json' 
--data-raw '{"key": "AKIA4TBFXCE34AW73XNB",
"secret": "YihtuoYFFWVmS5G8C+aCnS/mQK0nv8TIKbY+Zuhb",
"cluster_id": "j-1DFKHPI72XWX3"}'