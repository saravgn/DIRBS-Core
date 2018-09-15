"""
DIRBS DB schema migration script (v47 -> v48).

Copyright (c) 2018 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted (subject to the limitations in the disclaimer below) provided that the
following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions
   and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions
   and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse
   or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED
BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import logging

from psycopg2 import sql

import dirbs.schema_migrators
import dirbs.utils as utils


class SeenTripletsMSISDNIndexMigrator(dirbs.schema_migrators.AbstractMigrator):
    """Class use to upgrade to V47 of the schema (seen_triplets).

    Implement in Python since it requires adding indexes on msisdn column to all seen_triplets partitions
    and is harder to do using pure SQL.
    """

    def upgrade(self, db_conn):
        """Overrides AbstractMigrator upgrade method."""
        logger = logging.getLogger('dirbs.db')
        with db_conn.cursor() as cursor:
            child_table_names_list = utils.child_table_names(db_conn, 'seen_triplets')
            logger.info('Adding index to all partitions of seen_triplets table: '
                        '{0}'.format(', '.join(child_table_names_list)))
            for c in child_table_names_list:
                logger.info('Adding MSISDN index to table {0}...'.format(c))
                cursor.execute(sql.SQL("""CREATE INDEX {0} ON {1}(msisdn);""")
                               .format(sql.Identifier(c + '_msisdn_idx'),
                                       sql.Identifier(c)))
                logger.info('Added MSISDN index to table {0}'.format(c))

            logger.info('Added index to all partitions of seen_triplets table')


migrator = SeenTripletsMSISDNIndexMigrator