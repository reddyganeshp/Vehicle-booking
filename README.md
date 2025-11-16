# Vehicle Service Booking System

A comprehensive vehicle service booking system built with FastAPI and AWS services.

## Features

### CRUD Operations (Database Operations)
- ✅ Bookings Management
- ✅ Vehicles Management
- ✅ Customers Management
- ✅ Service Centers Management

### Non-CRUD Operations (Separate Library - No Database)
- ✅ **SNS** - Notification Service (booking confirmations, reminders, cancellations)
- ✅ **S3** - Storage Service (service reports, invoices, vehicle images)
- ✅ **SQS** - Queue Service (async booking processing)
- ✅ **EventBridge** - Scheduler Service (reminders, follow-ups)
- ✅ **Pure Logic** - Cost Calculator, Report Generator, Validator

## AWS Services Used

1. **DynamoDB** - Database for CRUD operations
2. **S3** - Document storage
3. **SNS** - Notifications
4. **SQS** - Message queuing
5. **EventBridge** - Event scheduling

## Installation

```bash
pip install -r requirements.txt