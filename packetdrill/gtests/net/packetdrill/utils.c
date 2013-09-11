#include "utils.h"

void seed_generator(){
	srand(time(NULL));
}

u64 rand_64(){
	seed_generator();
	u64 r;
	unsigned int *part1 = (unsigned int*)&r;
	unsigned int *part2 = &(((unsigned int*)&r)[1]);
	*part1 = rand();
	*part2 = rand();
	return r;
}

u32 generate_32(){
	seed_generator();
	return rand();
}

void hash_key_sha1(uint8_t *hash, key64 key) {
	SHA_CTX ctx;
	SHA1_Init(&ctx);
	SHA1_Update(&ctx, &key, sizeof(key));
	SHA1_Final(hash, &ctx);
}

key64 get_barray_from_key64(unsigned long long key)
{
	return *(key64 *)(unsigned char*)&key;
}

void hmac_sha1(const unsigned char *key,
		u32 key_length,
		char *data,
		u32 data_length,
		unsigned char *output)
{

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
		u32 key_length,
		char *data,
		u32 data_length)
{
	unsigned char hash[20];
	hmac_sha1(key, key_length, data, data_length, hash);
	u64 truncated = *((u64*)hash);
	return truncated;
}

u32 sha1_least_32bits(u64 key)
{
	key64 key_arr = get_barray_from_key64(key);
	u8 hash[SHA_DIGEST_LENGTH];
	hash_key_sha1(hash, key_arr);
	return ntohl(*((u32*)hash));
}

u64 sha1_least_64bits(u64 key)
{
	key64 key_arr = get_barray_from_key64(key);
	uint8_t hash[SHA_DIGEST_LENGTH];
	hash_key_sha1(hash, key_arr);
	return be64toh(*((u64*)hash)); //CPAASCH said [12]
}

u16 checksum(u16 *buffer, int size)
{
	unsigned long cksum=0;
	while(size >1)
	{
		cksum+=*buffer++;
		size -=sizeof(u16);
	}
	if(size)
		cksum += *(u8*)buffer;

	cksum = (cksum >> 16) + (cksum & 0xffff);
	cksum += (cksum >>16);
	return (u16)(~cksum);
}
