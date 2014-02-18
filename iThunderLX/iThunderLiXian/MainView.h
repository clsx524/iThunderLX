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
#import "TorrentView.h"
#import "DropZoneView.h"

@interface MainView : NSWindowController <DropZoneDelegate>
{
    IBOutlet NSWindow *login_window;
    IBOutlet NSTextField *login_username;
    IBOutlet NSTextField *login_password;
    IBOutlet NSProgressIndicator *login_progress;
    IBOutlet NSButton *login_ok_button;
    //IBOutlet NSButton *button_add_bt_task;
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
    
    MessageView *message_view;
    TasksView *tasks_view;
    
    TorrentView *torrent_view;
    DropZoneView *drop_zone_view;
    
    IBOutlet NSTabView *torrent_tab_view;
    IBOutlet NSButton *torrent_ok_button;
    IBOutlet NSButton *torrent_back_button;
    IBOutlet NSButton *torrent_add_cancel_button;
    IBOutlet NSButton *torrent_select_all_button;
    IBOutlet NSButton *torrent_negative_select_button;
    
    int current_page;    
}
@property (atomic) int current_page;
@property (atomic, retain) NSString *hash;
@property (atomic, retain) NSString *cookie;

- (IBAction)add_torrent_file_button:(id)sender;
- (IBAction)torrent_add_confirm_button:(id)sender;
- (IBAction)torrent_add_back_button:(id)sender;
- (IBAction)torrent_add_cancel_button:(id)sender;
- (IBAction)toolbar_add_task:(id)sender;
- (void)didReceivedTorrentFile: (NSString*)filePath;
- (void)upload_torrent_file: (NSString*)filePath;
- (BOOL)add_task_panel_is_open;
@end
