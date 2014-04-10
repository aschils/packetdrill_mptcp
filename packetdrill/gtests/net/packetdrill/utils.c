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

void hmac_sha1_truncat_64(const unsigned char *key,
		u32 key_length,
		char *data,
		u32 data_length, unsigned char* hash)
{
//	unsigned char hash[20];
	hmac_sha1(key, key_length, data, data_length, hash);
//	return hash; //*((u64*)hash);
//	return truncated;
}

u32 sha1_least_32bits(u64 key)
{
	key64 key_arr = get_barray_from_key64(key);
	u8 hash[SHA_DIGEST_LENGTH];
	hash_key_sha1(hash, key_arr);
	return (u32)be32toh(*((u32*)hash)); // = ntohl
}

u64 sha1_least_64bits(u64 key)
{
	key64 key_arr = get_barray_from_key64(key);
	uint8_t hash[SHA_DIGEST_LENGTH];
	hash_key_sha1(hash, key_arr);
//	printf("%x%x --- %x%x-%x%x\n", *((u8*)&hash[0]), *((u8*)&hash[1]), *((u8*)&hash[12]), *((u8*)&hash[13]), *((u8*)&hash[18]), *((u8*)&hash[19]));
//	printf("%llx%llx%x\n", (u64)be64toh(*((u64*)&hash[0])), (u64)be64toh(*((u64*)&hash[8])), (u32)be32toh(*((u32*)&hash[16])));
//	printf("%llx \n", (u64)be64toh(*((u64*)&hash[12])));
//	printf("%llx \n", (u64)be64toh(*((u64*)&hash[12])));
	return (u64)be64toh(*((u64*)&hash[12]));
}

u16 checksum_dss(u16 *buffer, int size)
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

uint16_t checksum_d(void* vdata, size_t length) {
    // Cast the data pointer to one that can be indexed.
    char* data=(char*)vdata;
    size_t i;
    // Initialise the accumulator.
    uint32_t acc=0xffff;

    // Handle complete 16-bit blocks.
    for (i=0;i+1<length;i+=2) {
        uint16_t word;
        memcpy(&word,data+i,2);
        acc+=ntohs(word);
        if (acc>0xffff) {
            acc-=0xffff;
        }
    }

    // Handle any partial block at the end of the data.
    if (length&1) {
        uint16_t word=0;
        memcpy(&word,data+length-1,1);
        acc+=ntohs(word);
        if (acc>0xffff) {
            acc-=0xffff;
        }
    }

    // Return the checksum in network byte order.
    return ~acc;
}
