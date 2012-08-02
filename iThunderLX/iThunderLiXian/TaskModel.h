//
//  TaskModel.h
//  iThunderLiXian
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Foundation/Foundation.h>
#import "DownloadOperation.h"

@class DownloadOperation;
@interface TaskModel : NSObject {
    NSString *TaskTitle;
    NSString *FatherTitle;
    NSString *TaskSizeDescription;
    NSString *TaskLiXianProcess;
    NSString *TaskID;
    NSImage *TaskType;
    NSUInteger TaskSize;
    NSUInteger TaskDownloadedSize; //只有BT任务用来记录，其他时候忽略这个
    NSString *Cookie;
    BOOL Indeterminate;
    BOOL YunDelete;
    NSInteger ProgressValue;
    NSString *LeftDownloadTime;
    NSString *LiXianURL;

    NSString *TaskTypeString;
    NSString *CID;
    NSString *ButtonTitle;
    TaskModel *FatherTaskModel;
    
    BOOL ButtonEnabled;
    BOOL LeftTimeButtonHidden;
    
    DownloadOperation *download_operation;
    BOOL StartAllDownloadNow;
    @public
    BOOL NeedToStopNow;
    BOOL NeedToRestartNow;

}

@property (atomic) BOOL ButtonEnabled;
@property (atomic) BOOL LeftTimeButtonHidden;
@property (atomic) BOOL YunDelete;
@property (atomic, retain) NSString *ButtonTitle;
@property (atomic) NSUInteger TaskSize;
@property (atomic, retain) NSString *TaskTitle;
@property (atomic, retain) NSString *FatherTitle;
@property (atomic, retain) NSString *TaskSizeDescription;
@property (atomic, retain) NSString *TaskLiXianProcess;
@property (atomic, retain) NSString *LeftDownloadTime;
@property (atomic, retain) NSString *TaskID;
@property (atomic, retain) NSImage *TaskType;
@property (atomic) BOOL Indeterminate;
@property (atomic) NSInteger ProgressValue;
@property (atomic) NSUInteger TaskDownloadedSize;
@property (atomic, retain) NSString *Cookie;
@property (atomic, retain) NSString *LiXianURL;
@property (atomic, retain) NSString *TaskTypeString;
@property (atomic, retain) NSString *CID;
@property (atomic, retain) TaskModel *FatherTaskModel;
@property (atomic, retain) DownloadOperation *download_operation;
@property (atomic) BOOL StartAllDownloadNow;
-(void)start_download;
-(void)thread_delete_files;

@end
