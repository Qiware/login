#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <libwebsockets.h>

#include "sck.h"
#include "list.h"
#include "mesg.h"
#include "comm.h"
#include "cmd_list.h"
#include "mesg.pb-c.h"

#define AWS_SEND_BUF_LEN   (2048)  // 发送缓存的长度

#define SID (392)
char *TOKEN = "UHJTPARjW2pWMAc1BDcBa10jByUGMQQ/Cj1SNwVhUzZUNgE1BDZdZlc2AjgGPQYzAWVTYQ==";
char *APP = "websocket-test";
char *VERSION = "v.0.0.1";

/* 输入选项 */
typedef struct
{
    int num;                        /* 最大并发数 */
    uint32_t rid;                   /* 聊天室ID */
    int use_ssl;
    int port;
    int longlived;
    int ietf_version;
    int deny_deflate;
    char *ipaddr;
} wsc_opt_t;

/* 发送项 */
typedef struct
{
    size_t len;                     // 长度
    char addr[AWS_SEND_BUF_LEN];    // 发送内容
} wsc_send_item_t;

typedef struct
{
    list_t *send_list;
} wsc_session_data_t;

/* 全局对象 */
typedef struct
{
    wsc_opt_t opt;

    struct lws_context *lws;

    // 其他标志
    bool is_closed;
    bool is_force_exit;
} wsc_cntx_t;

static wsc_cntx_t g_wsc_cntx; /* 全局对象 */

/* 协议类型 */
typedef enum
{
    PROTOCOL_CHAT,

    /* always last */
    PROTOCOL_DEMO_COUNT
} demo_protocols;


int lws_online_handler(wsc_cntx_t *ctx, struct lws_context *lws, struct lws *wsi, wsc_session_data_t *session);

/* dumb_chat protocol */
static int callback_upload(
        struct lws_context *lws,
        struct lws *wsi,
        enum lws_callback_reasons reason,
        void *user, void *in, size_t len)
{
    int n;
    time_t ctm;
    struct tm lctm;
    //static int uid = 1234;
    char *param;
    mesg_header_t *head;
    wsc_send_item_t *item;
    wsc_cntx_t *ctx = &g_wsc_cntx;
    wsc_opt_t *opt = &ctx->opt;
    wsc_session_data_t *session = (wsc_session_data_t *)user;

    switch (reason) {
        case LWS_CALLBACK_CLIENT_ESTABLISHED:
            lws_online_handler(ctx, lws, wsi, session);
            break;
        case LWS_CALLBACK_CLIENT_CONFIRM_EXTENSION_SUPPORTED:
            fprintf(stderr, "callback_upload: LWS_CALLBACK_CLIENT_CONFIRM_EXTENSION_SUPPORTED\n");

            if ((strcmp(in, "deflate-stream") == 0) && opt->deny_deflate) {
                fprintf(stderr, "denied deflate-stream extension\n");
                return 1;
            }
            else if ((strcmp(in, "deflate-frame") == 0) && opt->deny_deflate) {
                fprintf(stderr, "denied deflate-frame extension\n");
                return 1;
            }
            break;
        case LWS_CALLBACK_CLIENT_RECEIVE:
            fprintf(stderr, "callback_upload: LWS_CALLBACK_CLIENT_RECEIVE\n");
            head = (mesg_header_t *)in;
            param = (char *)(head + 1);

            fprintf(stderr, "Recv data! cmd:0x%04X length:%d\n",
                    ntohl(head->type), ntohl(head->length));
            fprintf(stderr, "ReceiveData:%s \n", param);
			/* This line below is to test bullet screen off functions */

            ctm = time(NULL);
            localtime_r(&ctm, &lctm);
            fprintf(stderr, "year:%u mon:%u day:%u hour:%u min:%u sec:%u\n",
                    lctm.tm_year+1900, lctm.tm_mon+1, lctm.tm_mday,
                    lctm.tm_hour, lctm.tm_min, lctm.tm_sec);
            break;
        case LWS_CALLBACK_CLIENT_WRITEABLE:
            fprintf(stderr, "callback_upload: LWS_CALLBACK_CLIENT_WRITEABLE\n");
            while (1) {
                item = (wsc_send_item_t *)list_lpop(session->send_list);
                if (NULL == item) {
                    break;
                }

                n = lws_write(wsi, (unsigned char *)item->addr+LWS_SEND_BUFFER_PRE_PADDING,
                        item->len, LWS_WRITE_BINARY);
                if (n < 0) {
                    return -1;
                }
                else if (n < (int)item->len) {
                    lwsl_err("Partial write LWS_CALLBACK_CLIENT_WRITEABLE\n");
                    return -1;
                }
                free(item);
            }
            break;
        case LWS_CALLBACK_WSI_DESTROY:
            fprintf(stderr, "callback_upload: LWS_CALLBACK_WSI_DESTROY\n");
            ctx->is_closed = true;
        case LWS_CALLBACK_CLIENT_CONNECTION_ERROR:
            fprintf(stderr, "errmsg:%s\n", (char *)in);
            return -1;
        default:
            break;
    }

    return 0;
}

/* list of supported g_protocols and callbacks */
static struct lws_protocols g_protocols[] = {
    {
        "chat",
        callback_upload,
        sizeof(wsc_session_data_t),
        0,
    },
    { NULL, NULL, 0, 0 } /* end */
};

void sighandler(int sig)
{
    wsc_cntx_t *ctx = &g_wsc_cntx;

    ctx->is_force_exit = true;
}

/* Get input options for websocket client */
static int wsc_getopt(int argc, char *argv[], wsc_opt_t *opt)
{
    int n = 0;
    const struct option wsc_options[] = {
        {"help",        no_argument,        NULL,   'h'},
        {"debug",       required_argument,  NULL,   'd'},
        {"port",        required_argument,  NULL,   'p'},
        {"ssl",         no_argument,        NULL,   's'},
        {"version",     required_argument,  NULL,   'v'},
        {"undeflated",  no_argument,        NULL,   'u'},
        {"num",         no_argument,        NULL,   'n'},
        {"longlived",   no_argument,        NULL,   'l'},
        {"ipaddr",      no_argument,        NULL,   'i'},
        {"rid",         required_argument,  NULL,   'r'},
        {NULL,          0,                  0,      0}
    };

    memset(opt, 0, sizeof(wsc_opt_t));

    opt->num = 1;
    opt->ietf_version = 13;
    lws_set_log_level(0xFFFFFFFF, NULL);

    while (n >= 0) {
        n = getopt_long(argc, argv, "n:uv:i:r:hsp:d:l", wsc_options, NULL);
        if (n < 0) {
            continue;
        }
        switch (n) {
            case 'd':
                lws_set_log_level(atoi(optarg), NULL);
                break;
            case 's':
                opt->use_ssl = 2; /* 2 = allow selfsigned */
                break;
            case 'p':
                opt->port = atoi(optarg);
                break;
            case 'r':
                opt->rid = atoi(optarg);
                break;
            case 'l':
                opt->longlived = 1;
                break;
            case 'v':
                opt->ietf_version = atoi(optarg);
                break;
            case 'u':
                opt->deny_deflate = 1;
                break;
            case 'n':
                opt->num = atoi(optarg);
                break;
            case 'i':
                opt->ipaddr = optarg;
                break;
            case 'h':
                return -1;
        }
    }

    if (0 == opt->port
        || NULL == opt->ipaddr)
    {
        return -1;
    }

    return 0;
}

int main(int argc, char **argv)
{
    struct lws *wsi;
    int n = 0, ret = 0;
    struct lws_context *lws;
    wsc_cntx_t *ctx = &g_wsc_cntx;
    wsc_opt_t *opt = &ctx->opt;
    struct lws_context_creation_info info;

    fprintf(stderr, "libwebsockets test client\n"
            "(C) Copyright 2010-2015 Qifeng.zou <Qifeng.zou.job@hotmail.com> "
            "licensed under LGPL2.1\n");

    if (wsc_getopt(argc, argv, opt)) {
        goto usage;
    }

    //signal(SIGINT, sighandler);

    /*
     * create the websockets lws.  This tracks open connections and
     * knows how to route any traffic and which protocol version to use,
     * and if each connection is client or server side.
     *
     * For lws client-only demo, we tell it to not listen on any port.
     */
    memset(&info, 0, sizeof info);

    info.port = CONTEXT_PORT_NO_LISTEN;
    info.protocols = g_protocols;
#ifndef LWS_NO_EXTENSIONS
    info.extensions = lws_get_internal_extensions();
#endif
    info.gid = -1;
    info.uid = -1;

    lws = lws_create_context(&info);
    if (NULL == lws) {
        fprintf(stderr, "Creating libwebsocket lws failed\n");
        return -1;
    }

    /* create a client websocket using chat protocol */
    for (n=0; n<opt->num; n++) {
        wsi = lws_client_connect(lws, opt->ipaddr, opt->port, 0,
                "/upload", opt->ipaddr, opt->ipaddr,
                g_protocols[PROTOCOL_CHAT].name, opt->ietf_version);
        if (NULL == wsi) {
            fprintf(stderr, "libwebsocket connect failed\n");
            ret = 1;
            goto bail;
        }
    }

    fprintf(stderr, "Waiting for connect...\n");

    /*
     * sit there servicing the websocket lws to handle incoming
     * packets, and drawing random circles on the mirror protocol websocket
     * nothing happens until the client websocket connection is
     * asynchronously established
     */

    n = 0;
    while (n >= 0 && !ctx->is_force_exit && !ctx->is_closed) {
        n = lws_service(lws, 10);
    }

bail:
    fprintf(stderr, "Exiting\n");

    lws_context_destroy(lws);

    return ret;

usage:
    fprintf(stderr, "Usage: libwebsockets-test-client "
            "<server ip> [--port=<p>] "
            "[--ssl] [-k] [-v <ver>] "
            "[-d <log bitfield>] [-l]\n");
    return 1;
}

////////////////////////////////////////////////////////////////////////////////
// 上线请求
int lws_online_handler(wsc_cntx_t *ctx,
        struct lws_context *lws, struct lws *wsi, wsc_session_data_t *session)
{
    uint32_t len;
    list_opt_t lo;
    mesg_header_t *head;
    wsc_send_item_t *item;
    MesgOnline online = MESG_ONLINE__INIT;

    /* 创建发送队列 */
    online.sid = SID;
    online.token = TOKEN;
    online.app = APP;
    online.version = VERSION;

    len = mesg_online__get_packed_size(&online);

    /* 创建发送队列 */
    memset(&lo, 0, sizeof(lo));

    lo.pool = NULL;
    lo.alloc = mem_alloc;
    lo.dealloc = mem_dealloc;

    session->send_list = list_creat(&lo);
    if (NULL == session->send_list) {
        fprintf(stderr, "Create list failed!\n");
        return -1;
    }

    fprintf(stderr, "callback_upload: LWS_CALLBACK_CLIENT_ESTABLISHED\n");

    // 创建登录消息
    item = (wsc_send_item_t *)calloc(1, sizeof(wsc_send_item_t));
    if (NULL == item) {
        fprintf(stderr, "errmsg:[%d] %s!\n", errno, strerror(errno));
        return -1;
    }

    head = (mesg_header_t *)(item->addr + LWS_SEND_BUFFER_PRE_PADDING);

    head->type = htonl(CMD_ONLINE);
    head->sid = htonl(SID);
    head->seq = htonl(1);
    head->length = htonl(len);

    item->len = sizeof(mesg_header_t) + len;

    mesg_online__pack(&online, (void *)(head + 1));

    list_rpush(session->send_list, item);

    lws_callback_on_writable(lws, wsi);

    return 0;
}
