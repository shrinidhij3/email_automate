# CSV Upload Instructions

## Required CSV Format

Your CSV file must contain the following columns in the exact order:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| name | Yes | Full name of the person | John Doe |
| email | Yes | Email address of the person | john.doe@gmail.com |
| client_email | Yes | Client's email address | client@company.com |

## Example CSV File

```csv
name,email,client_email
John Doe,john.doe@gmail.com,client@company.com
Jane Smith,jane.smith@yahoo.com,client@company.com
Mike Johnson,mike.johnson@hotmail.com,client@company.com
Sarah Wilson,sarah.wilson@outlook.com,client@company.com
David Brown,david.brown@icloud.com,client@company.com
```

## Important Notes

1. **Header Row**: The first row must contain the column names exactly as shown above
2. **Case Sensitivity**: Column names are case-insensitive but must match exactly
3. **Email Validation**: All email addresses will be validated for proper format
4. **Duplicate Detection**: Duplicate emails in the same file will be skipped
5. **File Size**: Maximum file size is 10MB
6. **Encoding**: Use UTF-8 encoding for best compatibility

## Common Issues

- **Missing Required Fields**: All three columns (name, email, client_email) are required for each row
- **Invalid Email Format**: Ensure all email addresses follow standard email format (user@domain.com)
- **Empty Rows**: Empty rows will be automatically skipped
- **Special Characters**: Names can contain special characters, but emails should be standard format

## Auto-fill Feature

When you log in, the system will automatically fill the `client_email` field in forms with your registered email address for convenience.

## Download Example

You can download the example CSV file (`demo_emails.csv`) from the root directory to use as a template for your own uploads. 