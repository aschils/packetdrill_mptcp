#ifndef __TYPES_H_INCLUDED__
#define __TYPES_H_INCLUDED__
#include <time.h>
#include <stdlib.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include "types.h"

/**
 * A key is represented as a byte array of length 8.
 */
typedef struct { uint8_t data[8]; } key64, dsn64;
typedef struct { uint8_t data[4]; } token32;
typedef unsigned char uint8_t;


void seed_generator();
u64 generate_key64();
unsigned generate_32();
u32 get_token_32(u64 key);
void hash_key_sha1(uint8_t *hash, key64 key);
key64 get_barray_from_key64(unsigned long long key);
dsn64* retreive_dsn(uint8_t *hash);
token32 retreive_token(uint8_t *hash);
u64 hmac_sha1_truncat_64(const unsigned char *key,
		unsigned key_length,
		char *data,
		unsigned data_length);
void hmac_sha1(const unsigned char *key,
		unsigned key_length,
		char *data,
		unsigned data_length,
		unsigned *output);

#endif

