#s3bucketupload 
------

s3bucketupload is a go program used to download an antire aws s3 bucket.
You can use like :

- Install aws go sdk:

**go get -u github.com/aws/aws-sdk-go/...**

- Configure a profile (with the right policy : you need a write and list access)

**aws configure --profile s3bucket-download**

**AWS Access Key ID [None]: <YOUR ACCESS KEY>**

**AWS Secret Access Key [None]: <YOUR SECRET KEY>**

**Default region name [None]: <YOUR REGION>**

**Default output format [None]: json**

- Run the program:

**$GOPATH/bin/s3bucketupload aws_profile_name bucket_name bucket_prefix file|directory preserveDirStructure'yes|no'**
