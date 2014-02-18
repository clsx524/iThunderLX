//
//  DropZoneView.h
//  fakeThunder
//
//  Created by Jiaan Fang on 12-12-12.
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@protocol DropZoneDelegate <NSObject>

@optional
- (void)didReceivedTorrentFile: (NSString*)filePath;

@end

@interface DropZoneView : NSView {
    BOOL highlight;
    BOOL wrong_file;
    BOOL not_single;
}
@property (nonatomic, assign) id <DropZoneDelegate> delegate;

@end
