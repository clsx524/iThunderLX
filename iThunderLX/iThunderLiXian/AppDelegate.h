//
//  AppDelegate.h
//  iThunderLiXian
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Cocoa/Cocoa.h>
#import "MainView.h"
#import "RequestSender.h"

@interface AppDelegate : NSObject <NSApplicationDelegate> {
    
    //如果不在这里提前声明，会被ARC直接自动释放，真头疼
    MainView *main_view;
    
    NSTask *python_task;

}

@end
