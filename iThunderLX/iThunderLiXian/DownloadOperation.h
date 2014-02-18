//
//  DownloadOperation.h
//  iThunderLiXian
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Foundation/Foundation.h>
#import "TaskModel.h"

@class TaskModel;

@interface DownloadOperation : NSOperation {
    TaskModel *task;
    BOOL _isFinish;
}

-(id)initWithTaskModel:(TaskModel *)t;

@end
