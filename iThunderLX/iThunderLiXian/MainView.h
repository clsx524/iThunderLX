//
//  MainView.h
//  iThunderLX
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Cocoa/Cocoa.h>
#import "TasksView.h"
#import "RequestSender.h"
#import "AppPrefsWindowsController.h"
#import "MessageView.h"

@interface MainView : NSWindowController
{
    
    TasksView *tasks_view;
    
    IBOutlet NSWindow *login_window;
    IBOutlet NSTextField *login_username;
    IBOutlet NSTextField *login_password;
    IBOutlet NSProgressIndicator *login_progress;
    IBOutlet NSButton *login_ok_button;
    IBOutlet NSWindow *add_task_window;
    IBOutlet NSProgressIndicator *add_task_progress;
    IBOutlet NSButton *add_task_ok_button;
    IBOutlet NSTextField *add_task_url;
    IBOutlet NSToolbarItem *toobaritem_login;
    IBOutlet NSToolbarItem *toobaritem_loadmore;
    IBOutlet NSToolbarItem *toobaritem_add_task;
    IBOutlet NSToolbarItem *toobaritem_refresh;
    IBOutlet NSToolbarItem *toobaritem_yundelete;
    NSString *hash;
    NSString *cookie;
    //BOOL checkboxEnabled;
    
    MessageView *message_view;
    
    int current_page;
    
}
@property (atomic) int current_page;
@property (atomic, retain) NSString *hash;
@property (atomic, retain) NSString *cookie;

@end
