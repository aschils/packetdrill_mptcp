#include "utils.h"

void seed_generator(){
	srand(time(NULL));
}

//rand() value is library-dependent,
//but is guaranteed to be at least 32767 
u64 generate_key64(){
	u64 r;
	unsigned int *part1 = (unsigned int*)&r;
	unsigned int *part2 = &(((unsigned int*)&r)[1]);
	*part1 = rand();
	*part2 = rand();
	return r;
}

unsigned generate_32(){
	seed_generator();
	return rand();
}

void hash_key_sha1(uint8_t *hash, key64 key) {
	SHA_CTX ctx;
	SHA1_Init(&ctx);
	SHA1_Update(&ctx, &key, sizeof(key));
	SHA1_Final(hash, &ctx);
}

key64 get_barray_from_key64(unsigned long long key){
	return *(key64 *)(unsigned char*)&key;
}

dsn64* retreive_dsn(uint8_t *hash){
	return (dsn64*)(hash+12); //to get the last 64 bits from hash
}

token32 retreive_token(uint8_t *hash){
	return *(token32*)hash;  // to get the first 32 bits
}

void hmac_sha1(const unsigned char *key,
		unsigned key_length,
		char *data,
		unsigned data_length,
		unsigned *output){

	unsigned char* hash;

	hash = HMAC(EVP_sha1(),
			key, key_length,
			(unsigned char*)data,
			data_length,
			NULL,
			NULL);
	memcpy(output, hash, 20);
}

u64 hmac_sha1_truncat_64(const unsigned char *key,
		unsigned key_length,
		char *data,
		unsigned data_length)
{
	unsigned char* hash;

	hash = HMAC(EVP_sha1(),
			key, key_length,
			(unsigned char*)data,
			data_length,
			NULL,
			NULL);

	u64 truncated = *((u64*)hash);
	return truncated;
}

u32 get_token_32(u64 key){
	key64 key_arr = get_barray_from_key64(key);
	uint8_t hash[SHA_DIGEST_LENGTH];
	hash_key_sha1(hash, key_arr);
	token32 tokA = retreive_token(hash);
	return *((unsigned*)(tokA.data));
}

/*
 // a compiler avec gcc utils.c -o utils.o -lcrypto -std=c99
int main(){
	// *(key64 *)((uint8_t[8]){55, 0, 0, 0, 0, 0, 0, 1});
	key64 key_arr = get_barray_from_key64(1234567890123456789);
	uint8_t hash[SHA_DIGEST_LENGTH];
	hash_key_sha1(hash, key_arr);

	// token 32 first bits
	token32 tokA = retreive_token(hash);
	// IDSN 64 last bits
	dsn64 *idsn = retreive_dsn(hash);

	for(int i=0;i<8;i++){
		printf("[%X]",key_arr.data[i]);
	}
	printf(" hashed => ");
	for(int i=0;i<SHA_DIGEST_LENGTH;i++){
		printf("[%X]",hash[i]);
	}
	printf("\n");
	printf("Token: ");
	for(int i=0;i<4;i++){
		printf("[%X]", tokA.data[i]);
	}
	printf(": hash= %llu", *(unsigned long long*)hash);
	printf("=> %u ", *(unsigned*)tokA.data); // pour récuperer le token en unsigned : 32 bits
	printf("\n");
	printf("IDSN : ");
	for(int i=0;i<8;i++){
		printf("[%X]", ((uint8_t*)idsn)[i]);
	}
	printf(": idsn= %lu", *(unsigned long*)idsn); // pour récuperer le idsn en unsigned long : 64 bits
	printf("\n");
	printf("");
	return 0;
}
*/


