//
//  DownloadOperation.m
//  iThunderLiXian
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import "DownloadOperation.h"

@implementation DownloadOperation

-(id)initWithTaskModel:(TaskModel *)t
{
    if (self = [super init]) {
        task = t;
        t.ButtonTitle = @"队列中...";
        _isFinish = NO;
    }
    return self;
}

-(void)start
{
    if (self.isCancelled) {
        _isFinish = YES;
    } else {
        _isFinish = NO;
        [task start_download];
        _isFinish = YES;
    }
}

-(BOOL)isFinished {
    return _isFinish;
}

@end
