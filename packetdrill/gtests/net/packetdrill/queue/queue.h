/*
 * Queue implementation based on circular array.
 *
 * queue.h
 *
 *  Created on: 28 juil. 2013
 *      Author: Arnaud Schils
 */

#ifndef __QUEUE_H__
#define __QUEUE_H__

#include <stdlib.h>

#define QUEUE_SIZE 255
#define STATUS_OK 0
#define STATUS_ERR -1

#ifndef NULL
#define NULL 0
#endif

struct queue_s{
	void *elements[QUEUE_SIZE];
	unsigned r, f;
};

typedef struct queue_s queue_t;

void queue_init(queue_t *queue);

void queue_free(queue_t *queue);

unsigned queue_size(queue_t *queue);

unsigned queue_is_empty(queue_t *queue);

int queue_front(queue_t *queue, void **element);

int queue_rear(queue_t *queue, void **element);

int queue_dequeue(queue_t *queue, void **element);

int queue_enqueue(queue_t *queue, void *element);

#endif
