//
//  AppPrefsWindowsController.m
//  iThunderLX
//
//  Created by Martian
//  Editd by Eric
//  Copyright (c) 2012年 CLSX524. All rights reserved.

#import "AppPrefsWindowsController.h"

@implementation AppPrefsWindowsController

-(void)setupToolbar
{
    [self addView:generalPreferenceView label:@"常规"];
    [self addView:advancedPreferenceView label:@"高级"];
    
    [self setCrossFade:YES];
	[self setShiftSlowsAnimation:YES];
    
    [[NSColorPanel sharedColorPanel] setShowsAlpha:YES];
    [NSColor setIgnoresAlpha:NO];
}

-(IBAction)selectSavePath:(id)sender
{
    NSPopUpButton *popup_button = (NSPopUpButton *)sender;
    if ([popup_button indexOfSelectedItem] == 2) {
        NSOpenPanel *panel = [NSOpenPanel openPanel];
        [panel setCanChooseFiles:NO];
        [panel setCanChooseDirectories:YES];
        [panel beginSheetModalForWindow:self.window completionHandler:^(NSInteger result) {
            if (result == NSFileHandlingPanelOKButton) {
                NSURL *url = panel.directoryURL;
                NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
                [defaults setObject:[url path] forKey:@UD_SAVE_PATH];
                [[popup_button itemAtIndex:0] setTitle:[[url path] lastPathComponent]];
                [defaults setObject:[[url path] lastPathComponent] forKey:@UD_SAVE_PATH_DISPLAY];
                
                [defaults synchronize];
            }
        }];
        
        [popup_button selectItemAtIndex:0];
    }
}

-(IBAction)setMaxTasks:(id)sender
{
    //NSInteger max_tasks = [[NSUserDefaults standardUserDefaults] integerForKey:@UD_MAX_TASKS];
    [[NSNotificationCenter defaultCenter] postNotificationName:@UD_MAX_TASKS object:self];
}

-(IBAction)deleteHashAndCookie:(id)sender
{
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:@"" forKey:@UD_LAST_LOGIN_HASH];
    [defaults setObject:@"" forKey:@UD_LAST_LOGIN_COOKIE];
    [defaults synchronize];
    
}

-(IBAction)donateButton:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://glurl.co/B8"]];
}

-(IBAction)openCLSX524_BLOG:(id)sender
{
    [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://clsx524.github.com"]];
}

-(IBAction)copyHashAndCookie:(id)sender
{
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];

    [[NSPasteboard generalPasteboard] declareTypes:[NSArray arrayWithObject: NSStringPboardType] owner:nil];
    [[NSPasteboard generalPasteboard] setString:[NSString stringWithFormat:@"%@\n%@",[defaults objectForKey:@UD_LAST_LOGIN_HASH],[defaults objectForKey:@UD_LAST_LOGIN_COOKIE]] forType: NSStringPboardType];
}
@end
