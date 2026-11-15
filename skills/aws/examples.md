# AWS Example: Upload a File to S3

```python
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3", region_name="ap-south-1")
try:
    s3.upload_file("report.csv", "my-bucket", "reports/report.csv")
except ClientError as error:
    print(error.response["Error"]["Code"])
```

Use an IAM role or configured AWS profile. Do not put access keys in source code.
