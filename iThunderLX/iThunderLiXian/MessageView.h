//
//  MessageView.h
//  iThunderLX
//
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Cocoa/Cocoa.h>
#import "TasksView.h"

@class TasksView;
@interface MessageView : NSViewController {
    IBOutlet NSTextField *message_label;
    IBOutlet NSProgressIndicator *message_progress;
    TasksView *tasks_view;
}

-(id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil TasksView:(TasksView *)tasksView;
-(void)showMessage:(NSString *)message;
-(void)hideMessage;


@end
