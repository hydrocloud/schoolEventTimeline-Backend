#include <stdio.h>
#include <string.h>

#include <list>

static std::list<char *> mem_allocations;

static bool debug_on = false;

static unsigned char *zhixue_pw_xor_key;
static size_t zhixue_pw_xor_key_size;

static const char zhixue_pw_xor_template_plain[] = "0000000000000000";
static const char zhixue_pw_xor_template_encrypted[] = "5598d8718d0f56edc952d04612e13e16";

static void zhixue_get_xor_key() {
    int i;
    unsigned char parsed_a, parsed_b;

    zhixue_pw_xor_key_size = strlen(zhixue_pw_xor_template_plain);
    zhixue_pw_xor_key = new unsigned char [zhixue_pw_xor_key_size + 1];

    for(i=0; i<zhixue_pw_xor_key_size; i++) {
        parsed_a = zhixue_pw_xor_template_encrypted[i * 2] - '0';
        if(parsed_a > 9) parsed_a = zhixue_pw_xor_template_encrypted[i * 2] - 'a' + 10;

        parsed_b = zhixue_pw_xor_template_encrypted[i * 2 + 1] - '0';
        if(parsed_b > 9) parsed_b = zhixue_pw_xor_template_encrypted[i * 2 + 1] - 'a' + 10;

        zhixue_pw_xor_key[i] = zhixue_pw_xor_template_plain[i] ^ (parsed_a * 16 + parsed_b);
    }
}

extern "C" void init() {
    zhixue_get_xor_key();
}

extern "C" char * zhixue_pw_encode(const char *src) {
    int i = 0;
    size_t length = strlen(src);
    char *ret;

    if(length > zhixue_pw_xor_key_size) return NULL;

    ret = new char [length * 2 + 1];
    mem_allocations.push_back(ret);

    ret[length * 2] = '\0';

    for(i=0; i<length; i++) {
        sprintf(ret + i * 2, "%02x", src[i] ^ zhixue_pw_xor_key[i]);
    }

    return ret;
}

extern "C" void free_memory() {
    int free_count = 0;

    for(auto m : mem_allocations) {
        delete[] m;
        free_count++;
    }

    if(debug_on) {
        printf("%d references freed.\n",free_count);
    }

    mem_allocations.clear();
}