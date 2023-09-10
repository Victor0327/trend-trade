def get_list_sql(args):
    return f"""
    select
    *
    from trade_symbols
    where active_flag is true;
"""

def post_sql(args):
    return f"""
    INSERT INTO "public"."trade_opportunities"("symbol","interval","create_at","update_at","type","title","active_flag")
    VALUES
    ({args['version']},'{args['created_at']}',{args['canary_percentage']},NULL);
"""