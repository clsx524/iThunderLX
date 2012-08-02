//
//  AppPrefsWindowsController.h
//  iThunderLX
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import <Foundation/Foundation.h>
#import "DBPrefsWindowController.h"

@interface AppPrefsWindowsController : DBPrefsWindowController <NSWindowDelegate> {
    IBOutlet NSView *generalPreferenceView;
    IBOutlet NSView *advancedPreferenceView;
    
    @public
    NSOperationQueue *operation_download_queue;
}

@end
