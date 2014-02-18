//
//  RequestSender.h
//
//  Created by Martian

#import <Cocoa/Cocoa.h>

@interface RequestSender : NSObject {

}

+ (NSString*)sendRequest:(NSString*)url;
+ (NSString*)postRequest:(NSString*)url withBody:(NSString *)data;

@end
