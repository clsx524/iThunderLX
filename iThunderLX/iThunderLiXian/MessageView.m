//
//  MessageView.m
//  iThunderLX
//
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import "MessageView.h"

@interface MessageView ()

@end

@implementation MessageView

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil TasksView:(TasksView *)tasksView
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        [self.view setHidden:YES];
        tasks_view = tasksView;
    }
    
    return self;
}

-(void) showMessage:(NSString *)message {
    [tasks_view.view setHidden:YES];
    [message_label setStringValue:message];
    [message_progress startAnimation:self];
    [self.view setHidden:NO];
}

-(void) hideMessage {
    [self.view setHidden:YES];
    [message_progress startAnimation:self];
    [tasks_view.view setHidden:NO];
}

@end
