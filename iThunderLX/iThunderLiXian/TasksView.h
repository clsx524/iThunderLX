//
//  TasksView.h
//  iThunderLX
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Cocoa/Cocoa.h>
#import "RequestSender.h"
#import "TaskModel.h"
#import "MessageView.h"

@class MessageView;

@interface TasksView : NSViewController {
    IBOutlet NSArrayController *array_controller;

    IBOutlet NSView *collection_view;
    IBOutlet NSBox *collection_view_box;
    IBOutlet NSCollectionView *collection;
    
    IBOutlet NSMenu *task_menu;
    IBOutlet NSButton *task_more_button;
    
    IBOutlet NSImageCell *nav_image;
    IBOutlet NSTextField *nav_label;
    IBOutlet NSButton *nav_button;
    
    IBOutlet NSButton *check_for_delete;

    NSOperationQueue *operation_download_queue;
    NSMutableArray *mutable_array;
    NSString *delete_files_list;
    NSMutableDictionary *bt_file_list_mutable_dict;
    
    NSString *hash;
    NSString *cookie;
    
    MessageView *message_view;
    
}

@property (atomic, retain) NSString *hash;
@property (atomic, retain) NSString *cookie;

- (void)thread_get_task_list:(NSInteger)page_num;
- (BOOL)thread_add_task:(NSString *)task_url;
- (void)thread_delete_yunfile;
- (void)clear_task_list;
- (BOOL)thread_check_downloading;
- (void)thread_nav_button_Hidden:(BOOL)state;

@end
